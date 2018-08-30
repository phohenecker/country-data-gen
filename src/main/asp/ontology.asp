% 2-Clause BSD License
%
% Copyright (c) 2018, Patrick Hohenecker
% All rights reserved.
%
% Redistribution and use in source and binary forms, with or without
% modification, are permitted provided that the following conditions are met:
%
% 1. Redistributions of source code must retain the above copyright notice, this
%    list of conditions and the following disclaimer.
% 2. Redistributions in binary form must reproduce the above copyright notice,
%    this list of conditions and the following disclaimer in the documentation
%    and/or other materials provided with the distribution.
%
% THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
% ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
% WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
% DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
% ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
% (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
% LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
% ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
% (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
% SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

% author:   Patrick Hohenecker (mail@paho.at)
% version:  2018.1


%%%%%%%% SAFETY RULES %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

:- country(X), region(X)                                                                .
:- country(X), subregion(X)                                                             .
:- region(X), subregion(X)                                                              .
:- locatedIn(C, S1), locatedIn(C, S2), country(C), subregion(S1), subregion(S2), S1!=S2 .
:- locatedIn(C, R1), locatedIn(C, R2), country(C), region(R1), region(R2), R1!=R2       .
:- locatedIn(S, R1), locatedIn(S, R2), subregion(S), region(R1), region(R2), R1!=R2     .
:- neighborOf(R, _), region(R)                                                          .
:- neighborOf(_, R), region(R)                                                          .
:- neighborOf(S, _), subregion(S)                                                       .
:- neighborOf(_, S), subregion(S)                                                       .


%%%%%%%% CLASSES %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

~region(X)    :- country(X)   .
~subregion(X) :- country(X)   .
~country(X)   :- region(X)    .
~subregion(X) :- region(X)    .
~country(X)   :- subregion(X) .
~region(X)    :- subregion(X) .


%%%%%%%% LOCATED-IN %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% inferable types
country(C)   :- locatedIn(C, S), subregion(S)              .
region(R)    :- locatedIn(S, R), subregion(S)              .
region(R)    :- locatedIn(C, R), country(C), ~subregion(R) .
subregion(S) :- locatedIn(C, S), country(C), ~region(S)    .
country(C)   :- locatedIn(C, S), locatedIn(S, R)           .
subregion(S) :- locatedIn(C, S), locatedIn(S, R)           .
region(R)    :- locatedIn(C, S), locatedIn(S, R)           .

% every country is located in at most one subregion
~locatedIn(C, S2) :- locatedIn(C, S1), subregion(S1), subregion(S2), S1!=S2 .

% every country/subregion is located in at most one region
~locatedIn(X, R2) :- locatedIn(X, R1), region(R1), region(R2), R1!=R2 .

% no country in one region is located in another region's subregions
% (this rule is needed in addition to the previous one, since there exist regions without subregions)
~locatedIn(C, S) :- locatedIn(C, R1), locatedIn(S, R2), country(C), region(R1), subregion(S), R1!=R2 .

% transitivity
locatedIn(C, R) :- locatedIn(C, S), locatedIn(S, R) .


%%%%%%%% NEIGHBOR-OF %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% inferable types
country(C) :- neighborOf(C, _) .
country(C) :- neighborOf(_, C) .

% neighborOf is symmetric
neighborOf(C2, C1)  :- neighborOf(C1, C2)  .
~neighborOf(C2, C1) :- ~neighborOf(C1, C2) .

% all neighborOf relations are specified explicitly (at least one direction)
~neighborOf(C1, C2) :- country(C1), country(C2), C1!=C2, not neighborOf(C1, C2) .
